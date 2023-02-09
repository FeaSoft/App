include 'mkl_spblas.f90'

! Description:
! Main program.
program fs_solver
    use data_model
    use execution_model
    use input_output
    implicit none
    
    integer                     :: argc    ! command line arguments count
    character(256), allocatable :: argv(:) ! command line arguments vector
    character(8)                :: date    ! current date
    character(10)               :: time    ! current time
    type(t_mdb)                 :: mdb     ! model database
    type(t_odb)                 :: odb     ! output database
    integer                     :: i       ! loop counter
    
    ! get command line arguments
    argc = command_argument_count() + 1
    allocate(argv(argc))
    do i = 1, argc
        call get_command_argument(i - 1, argv(i))
    end do
    
    ! print info
    call date_and_time(date, time)
    print '("Solver has started")'
    print '(A,"-",A,"-",A," ",A,":",A,":",A)', date(1:4), date(5:6), date(7:8), time(1:2), time(3:4), time(5:6)
    print '("")'
    
    ! read solver job input
    print '("Loading solver job input from file: ''",A,"''")', trim(argv(1))
    mdb = read_input(trim(argv(1)))
    print '("Solver job input loaded")'
    print '("")'
    
    ! compute algebraic connectivity
    print '("Building algebraic connectivity")'
    call mdb%build_dofs()
    print '("Active degrees of freedom: ",I0)', mdb%n_adofs
    print '("Inactive degrees of freedom: ",I0)', mdb%n_idofs
    print '("")'
    
    ! perform static analysis
    print '("Performing static analysis")'
    odb = static_analysis(mdb)
    print '("Static analysis successfully performed")'
    print '("")'
    
    ! write output database
    print '("Saving output database to file: ''",A,"''")', trim(argv(2))
    call write_output(trim(argv(2)), mdb%mesh, odb)
    print '("Output database saved")'
    print '("")'
    
    ! done
    if (allocated(argv)) deallocate(argv)
    print '("Solver is done")'
    
end program
