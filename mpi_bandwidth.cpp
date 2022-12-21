#include <mpi.h>
#include <iostream>
#include <memory>
#include <chrono>
#include <vector>
#include <algorithm>



std::vector<int> comm_schedule(MPI_Comm comm) {
  int rank, size;
  MPI_Comm_rank(comm, &rank);
  MPI_Comm_size(comm, &size);
  std::vector<int> msgs;
  for (int r = 0; r < size; ++r) {
    msgs.push_back((r + rank) % size);
  }
  std::vector<int> schedule(size);
  for (int r = 0; r < size; ++r) {
    schedule[msgs[r]] = r;
  }
  return schedule;
}





int main(int argc, char *argv[]) {
  MPI_Init(&argc, &argv);
  int size, rank;
  MPI_Comm_size(MPI_COMM_WORLD, &size);
  MPI_Comm_rank(MPI_COMM_WORLD, &rank);

  // Each rank schould send up to 1GB of data to the other ranks
  static constexpr size_t KB = 1024;
  static constexpr size_t MB = 1024 * 1024;
  static constexpr size_t GB = 1024 * 1024 * 1024;
  const size_t max_msg_size = std::min(32*GB / size, 2*GB);
  for (size_t msg_size = KB ; msg_size < max_msg_size; msg_size <<= 1) {
    if (rank == 0) {
      std::cout << "\nMessage Size: ";
      if (msg_size < MB) {
	std::cout << msg_size/KB << "KB";
      } else if (msg_size < GB) {
	std::cout << msg_size/MB << "MB";
      } else {
	std::cout << msg_size/GB << "GB";
      }
      std::cout << std::endl;
    }
    size_t num_bytes = size * msg_size;
    auto senddata = std::make_unique<char[]>(num_bytes);
    auto recvdata = std::make_unique<char[]>(num_bytes);

    // Measure the performance of MPI_Alltoall
    std::vector<double> speed_alltoall;
    for (int i = 0 ; i < 100 ; ++i) {
      MPI_Barrier(MPI_COMM_WORLD);
      const auto start = std::chrono::steady_clock::now();
      MPI_Alltoall(senddata.get(), msg_size, MPI_CHAR, recvdata.get(), msg_size, MPI_CHAR, MPI_COMM_WORLD);
      MPI_Barrier(MPI_COMM_WORLD);
      const auto end = std::chrono::steady_clock::now();
      const double elapsed = std::chrono::duration_cast<std::chrono::duration<double>>(end - start).count();
      speed_alltoall.push_back(static_cast<double>(num_bytes)/GB/elapsed);
    }
    std::sort(speed_alltoall.begin(), speed_alltoall.end());
    if (rank == 0) {
      std::cout << "MPI_Alltoall Max Speed: " << speed_alltoall.back() << "GB/s" << std::endl;
    }

    // Measure the performance of doing an alltoall with a series of MPI_Sendrecv
    const std::vector<int> schedule = comm_schedule(MPI_COMM_WORLD);
    std::vector<double> speed_sendrecv;
    for (int i = 0 ; i < 100 ; ++i) {
      MPI_Barrier(MPI_COMM_WORLD);
      const auto start = std::chrono::steady_clock::now();
      for (size_t r: schedule) {
	char *senddata_start = senddata.get() + r * msg_size;
	char *recvdata_start = recvdata.get() + r * msg_size;
	MPI_Sendrecv(senddata_start, msg_size, MPI_CHAR, r, 0, recvdata_start, msg_size, MPI_CHAR, r, 0, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
      }
      MPI_Barrier(MPI_COMM_WORLD);
      const auto end = std::chrono::steady_clock::now();
      const double elapsed = std::chrono::duration_cast<std::chrono::duration<double>>(end - start).count();
      speed_sendrecv.push_back(static_cast<double>(num_bytes)/GB/elapsed);
    }
    std::sort(speed_sendrecv.begin(), speed_sendrecv.end());
    if (rank == 0) {
      std::cout << "MPI_Sendrecv Max Speed: " << speed_sendrecv.back() << "GB/s" << std::endl;
    }
  }

  MPI_Finalize();
  return 0;
}
